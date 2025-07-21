load C:\Users\Nkris\Programming\PrionPredictorDB\pipeline\output\Q13148.pdb, main
load C:\Users\Nkris\Programming\PrionPredictorDB\pipeline\output\Q13148_centroids.pdb, centroids
show spheres, centroids
set sphere_scale, 0.6, centroids
select cluster_0, centroids and ((resi 311) or (resi 313) or (resi 315) or (resi 316) or (resi 317) or (resi 318) or (resi 321) or (resi 322) or (resi 323) or (resi 325))
set_color cluster_color_0, [1.00, 0.30, 0.30]
color cluster_color_0, cluster_0
show spheres, cluster_0
set sphere_scale, 0.6, cluster_0
label cluster_0, resi
select cluster_1, centroids and ((resi 330) or (resi 333) or (resi 334) or (resi 336) or (resi 337) or (resi 339) or (resi 340))
set_color cluster_color_1, [0.30, 1.00, 0.30]
color cluster_color_1, cluster_1
show spheres, cluster_1
set sphere_scale, 0.6, cluster_1
label cluster_1, resi
select cluster_2, centroids and ((resi 382) or (resi 383) or (resi 385))
set_color cluster_color_2, [0.30, 0.30, 1.00]
color cluster_color_2, cluster_2
show spheres, cluster_2
set sphere_scale, 0.6, cluster_2
label cluster_2, resi
zoom main or centroids