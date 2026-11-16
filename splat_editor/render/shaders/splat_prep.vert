float a = cov[0][0] + 0.3;
float b = cov[0][1];
float c = cov[1][1] + 0.3;

float mid = 0.5 *(a + c);
float radius = length(vec2(0.5 * (a-c), b));
float lambda1 = mid + radius;
float lambda2 = max(mid- radius, 0.1);
vec2 axis1 =
vec2 axis2 = 
vec toNdc = 
vec2 major =
vec2 minor = 


mat3 quatToMat3(vec4 q) {
    float w = q.x, x= q.y, y = q.z, z= q.w;
    return mat3(1.0 -2.0*(y*y + z*z),2.0*(x*y+w*z),2.0*(x*z - w*y),
                2.0*(x*y-w*z),1.0-2.0*(x*x+z*z),2.0*(y*z+w*x),
                2.0* (x*z+w*y),2.0*(y*z-w*x), 1.0 - 2.0*(x*x + y*y));
}

mat covariance3D(mat3 R, vec3 scale) {
    mat3 M = R * mat3(scale.x, 0.0, 0.0, 0.0, scale.y, 0.0, 0.0, 0.0, scale.z);
    return M * transpose(M);
}

mat3 projectCovariance(mat3 sigma, vec3 viewPos, mat3 linear) {
    float vx = viewPos.x, vy = viewPos.y, vz = viewPos.z;
    mat3 J = mat3(uFocal / -vz, 0.0, 0.0, 
                  0.0, uFocal / -vz, 0.0,
                  uFocal * vx / (vz * vz), uFocal * vy / (vz * vz), 0.0)
    mat3 T = J* mat3(uModelView) * linear;
    return T * sigma * transpose(T);
}


vec3 shCoeff(in splat, int k) {
    return (texelFetch(uSh, splat * uShCount +k).rgb * 255.0 - 128.0)* uShScale;

}

vec3 shColor(int splat, vec3 d) {

}

vec3 color = vec3(rg, ba.x);
if (uShDegree > 0) color += shColor(splat, normalize(transpose(linear)* (center - uCamPos)));
color = clamp(color, 0.0, 1.0);



vec3 shade() {

}

float shadowFactor(vec3 worldPos, vec3 n) {
    
}