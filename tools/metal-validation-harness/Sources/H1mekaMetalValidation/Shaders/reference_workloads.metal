#include <metal_stdlib>
using namespace metal;

kernel void h1meka_vector_add(
    device const float *a [[buffer(0)]],
    device const float *b [[buffer(1)]],
    device float *out [[buffer(2)]],
    uint id [[thread_position_in_grid]]
) {
    out[id] = a[id] + b[id];
}

kernel void h1meka_saxpy(
    device const float *x [[buffer(0)]],
    device const float *y [[buffer(1)]],
    constant float &alpha [[buffer(2)]],
    device float *out [[buffer(3)]],
    uint id [[thread_position_in_grid]]
) {
    out[id] = alpha * x[id] + y[id];
}

kernel void h1meka_square(
    device const float *x [[buffer(0)]],
    device float *out [[buffer(1)]],
    uint id [[thread_position_in_grid]]
) {
    out[id] = x[id] * x[id];
}

kernel void h1meka_vector_multiply(
    device const float *a [[buffer(0)]],
    device const float *b [[buffer(1)]],
    device float *out [[buffer(2)]],
    uint id [[thread_position_in_grid]]
) {
    out[id] = a[id] * b[id];
}

kernel void h1meka_vector_subtract(
    device const float *a [[buffer(0)]],
    device const float *b [[buffer(1)]],
    device float *out [[buffer(2)]],
    uint id [[thread_position_in_grid]]
) {
    out[id] = a[id] - b[id];
}

kernel void h1meka_axpby(
    device const float *x [[buffer(0)]],
    device const float *y [[buffer(1)]],
    constant float &alpha [[buffer(2)]],
    constant float &beta [[buffer(3)]],
    device float *out [[buffer(4)]],
    uint id [[thread_position_in_grid]]
) {
    out[id] = alpha * x[id] + beta * y[id];
}
