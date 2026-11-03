#include <cstdint>

// 该缓冲区由外部 DMA 控制器写入，使用 volatile 限定
volatile uint8_t g_dma_buffer[64];

void dma_transfer_complete() {
    g_dma_buffer[0] = 0xFF;
}

int main() {
    return g_dma_buffer[0] ? 0 : 1;
}
