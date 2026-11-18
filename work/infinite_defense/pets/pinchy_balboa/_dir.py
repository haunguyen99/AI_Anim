for n in ("new_scene","open_scene"):
    print(n, (getattr(api,n).__doc__ or '')[:400])
