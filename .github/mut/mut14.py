"""v14 mutants on a copy of the built index.html: python mut14.py <copy of repo> <outdir> <names comma separated or all>"""
import subprocess, sys, os
wt, outdir, which = sys.argv[1], sys.argv[2], sys.argv[3]
p = os.path.join(wt, "index.html")
orig = open(p, encoding="utf-8", newline="").read()
M = {
    'M0_unchanged': None,
    # v13 mutants still meaningful
    'X1_no_union_across_squares': ('if(a1!==b1)par[a1]=b1', 'if(a1!==b1){}'),
    'X2_open_side_ok': ('if(!si)for(let cI=0;cI<I.n;cI++)if(reach[cI]&&!touch[cI])bad[I.base+cI]=1', '{}'),
    'X3_bad_not_shared_in_piece': ('if(bad[g])rb[r]=1', 'if(bad[g])rb[g]=1'),
    'X4_no_confirmed_contact_needed': ('if(rg[r]&&!rb[r])m[i]=1', 'if(!rb[r])m[i]=1'),
    'X6_any_own_copy_target': ('c===JMFIX_SKIP||sure(e,c)', 'true'),
    'X7_no_0_-1_target_exception': ('||c===JMFIX_SKIP||sure(e,c)', '||sure(e,c)'),
    'X8_donor_mask_ignored': ('const hm=dm(h);if(hm&&!hm[i>>2])continue;', ''),
    'X9_any_neighbour_tile_confirms': ('si=site.has(nb),J=info.get(nk)', 'si=!info.has(nk)&&!!(await A(nk)),J=info.get(nk)'),
    'X9a_v13_any_neighbour_image_confirms': ('si=site.has(nb),J=info.get(nk)', 'si=!info.has(nk)&&(ks.includes(nk)||!!(await A(nk))),J=info.get(nk)'),
    'X10_left_out_not_listed': ('ok.set(k,m);if(left)part.add(k);', 'ok.set(k,m);'),
    'X11_0_-1_skipped_again': ('const day=k.startsWith("day/"),dm=', 'if(c===JMFIX_SKIP)continue;const day=k.startsWith("day/"),dm='),
    'X12_unshown_gives_whole': ('dm=e=>e.shown.has(c)?null:e.ok.get(k)', 'dm=e=>null'),
    # v14
    'Y1_no_next_run_check': ('if(near.get(e).has(c)){', 'if(false){'),
    'Y2_each_image_alone': ('const r=await jmFixKeep(e,w,x1);', 'const r={keep:[],cut:[]};for(const c of w){const q=await jmFixKeep(e,[c],x1);r.keep.push(...q.keep);r.cut.push(...q.cut)}'),
    'Y3_site_now_only': ('for(const site of [e.site,new Set([...e.site,...nd])])', 'for(const site of [e.site])'),
    'Y4_site_next_only': ('for(const site of [e.site,new Set([...e.site,...nd])])', 'for(const site of [new Set([...e.site,...nd])])'),
    'Y5_site_squares_as_now': ('const A=async k=>live.has(k)?live.get(k).al:await orig(k)', 'const A=async k=>live.has(k)&&!e.shown.has(sq(k))?live.get(k).al:await orig(k)'),
    'Y6_one_pass': ('for(const k of kill){live.delete(k);cut.push(k)}}', 'for(const k of kill){live.delete(k);cut.push(k)}break}'),
    'Y7_no_new_pixels_in_piece_rule': ('if(al[i]&&!(own&&own[i])&&V.has(q[i])){kill.add(k);break}', 'if(false){}'),
    'Y8_no_across_rule': ('if(c&&c.al[j]&&!(own&&own[j]))kill.add(nk)', '{}'),
    'Y9_no_becoming_shown_rule': ('if(side&&nd.has(nb))for(const x of live.keys())if(sq(x)===nb)kill.add(x)', '{}'),
    'Y10_not_near_neighbours': ('for(const [dx,dz] of JMFIX_SD)n.add((x+dx)+","+(z+dz))}return[e,n]', '}return[e,n]'),
    'Y11_flip_only_in_taken_images': ('if(!own||!pm)continue;', 'if(!own||!pm||!live.has(k))continue;'),
    'Y12_cut_not_listed': ('for(const k of r.cut)s.cut.push(e.label+" "+k);', ''),
    'Y13_cut_all_on_flip': ('if(!flip)break;if(!kill.size)', 'if(!flip)break;if(true)'),
}
env = dict(os.environ, PYTHONIOENCODING="utf-8")
names = list(M) if which == "all" else which.split(",")
for k in names:
    v = M[k]
    s = orig
    if v:
        assert s.count(v[0]) == 1, (k, s.count(v[0]))
        s = s.replace(v[0], v[1])
    open(p, "w", encoding="utf-8", newline="").write(s)
    r = subprocess.run([sys.executable, os.path.join(wt, "tests", "jm_fix_test.py")], capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    open(os.path.join(outdir, k + ".txt"), "w", encoding="utf-8").write(r.stdout + r.stderr)
    fl = [l for l in r.stdout.splitlines() if l.startswith("FAIL")]
    print(k, "exit", r.returncode, "last:", (r.stdout.strip().splitlines() or ["?"])[-1], "| FAIL:", len(fl), "| Traceback" if "Traceback" in r.stdout + r.stderr else "", flush=True)
    [print("    ", l[:170], flush=True) for l in fl]
open(p, "w", encoding="utf-8", newline="").write(orig)
