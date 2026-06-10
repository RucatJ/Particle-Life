
__kernel void update(
    __global float2* positions,
    __global float2* velocities,
    __global int* types,
    __global float* force_matrix,
    int n,
    float world_width,
    float world_height,
    float max_dist_sq,
    float min_dist_sq,
    float max_dist,
    float min_dist,
    int type_count,
    float force_scale,
    float density_limit
) {
    int i = get_global_id(0);
    if (i >= n) return;
    
    float2 pi = positions[i];
    float fx_total = 0.0f;
    float fy_total = 0.0f;
    
    float local_density = 0.0f;
    float local_n = 0;
    
    for (int j = 0; j < n; j++) {
        if (i == j) continue;
        
        float dx = positions[j].x - pi.x;
        float dy = positions[j].y - pi.y;
        
        if (dx > world_width / 2) dx -= world_width;
        if (dx < -world_width / 2) dx += world_width;
        if (dy > world_height / 2) dy -= world_height;
        if (dy < -world_height / 2) dy += world_height;
        
        float dist_sq = dx*dx + dy*dy;
        if (dist_sq < 1e-10f) continue;
        
        float force = 0.0f;
        float dist = sqrt(dist_sq);
        
        if (dist_sq <= min_dist_sq) {
            force = (dist - min_dist) * 5.0f;
        } else if (dist_sq <= max_dist_sq) {
            float f = force_matrix[types[j] * type_count + types[i]];
            force = f * ((max_dist/2.0f - fabs(max_dist/2.0f - (dist - min_dist))) / (max_dist/2.0f));
        }
        
        if (dist < max_dist) {
            local_n += 1;
            if (types[i] == types[j]) {
                local_density += 1.0f - (dist / max_dist);
            } else {
                local_density += 0.5f * (1.0f - dist / max_dist);
            }
        }
        
        float norm_x = dx / dist;
        float norm_y = dy / dist;
        
        fx_total += norm_x * force;
        fy_total += norm_y * force;
    }
    
    local_density /= local_n;
    
    float density_factor = 1.0f - min(max(0.0f, local_density - density_limit), 1.005f);
    
    fx_total *= density_factor;
    fy_total *= density_factor;
    
    velocities[i].x += fx_total * force_scale;
    velocities[i].y += fy_total * force_scale;
    
}