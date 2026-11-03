#include <cstdint>

// 该缓冲区由外部 DMA 控制器写入，但未使用 volatile 限定
uint8_t g_dma_buffer[64]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-12]

void dma_transfer_complete() {
    g_dma_buffer[0] = 0xFF;
}

int main() {
    return g_dma_buffer[0];
}
