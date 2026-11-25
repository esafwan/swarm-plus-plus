"""In-place DB rename for ONE site. UNTESTED generic version; rehearse on a cloned bench first.

Run per site, BEFORE migrate, with the renamed code on disk and web/workers stopped:
  bench --site S execute /path/db_rename.py --kwargs "{'old':'old_app','new':'new_app','old_module':'Old App','new_module':'New App','dry_run':1}"
Set dry_run 0 to apply. Rerun must report 0 rows. Backup first. Importing frappe hooks is avoided
(raw SQL only), because hooks cannot load until the registry is fixed.
"""
import frappe


def execute(old, new, old_module, new_module, dry_run=1):
    db = frappe.db
    total = 0

    def run(sql, vals=()):
        nonlocal total
        if dry_run:
            return
        db.sql(sql, vals)
        total += db.sql("select row_count()")[0][0]

    # registry
    run("update `tabInstalled Application` set app_name=%s where app_name=%s", (new, old))
    run("update `tabDefaultValue` set defvalue=replace(defvalue, %s, %s) where defkey='installed_apps'", (old, new))
    run("update `tabModule Def` set app_name=%s where app_name=%s", (new, old))
    run("update `tabModule Def` set name=%s, module_name=%s where name=%s", (new_module, new_module, old_module))
    # patch log, so patches do not rerun
    run("update `tabPatch Log` set patch=replace(patch, %s, %s) where patch like %s", (old + ".", new + ".", old + ".%"))
    # module columns and dotted paths across all text columns
    cols = db.sql("""select table_name, column_name from information_schema.columns
        where table_schema=database() and data_type in ('varchar','text','longtext','mediumtext','json')
        and table_name like 'tab%%' and table_name not in
        ('tabError Log','tabDeleted Document','tabComment','tabVersion','tabActivity Log','tabAccess Log')""")
    for t, c in cols:
        if c in ("module", "source_module"):
            run(f"update `{t}` set `{c}`=%s where `{c}`=%s", (new_module, old_module))
        run(f"update `{t}` set `{c}`=replace(`{c}`, %s, %s) where `{c}` like %s",
            (old + ".", new + ".", "%" + old + ".%"))
    # shipped JSON re-sync on migrate: reset modified so newer files win
    for t in ("tabWorkspace", "tabReport", "tabNumber Card", "tabDashboard Chart", "tabPage"):
        run(f"update `{t}` set modified='1970-01-02' where module=%s", (new_module,))
    if not dry_run:
        db.commit()
        for k in frappe.cache.get_keys("*"):  # site-scoped; never flushall
            frappe.cache.delete_value(k)
    print({"dry_run": dry_run, "rows_touched": total, "text_columns_scanned": len(cols)})
    print("Still to do by hand: frappe.rename_doc for docs named after the old brand (Workspace, Page, Dock, Chart Source)")
