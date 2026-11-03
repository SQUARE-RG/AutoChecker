#define ENABLE_FAST_PATH 1

#if defined(ENABLE_FAST_PATH)
#define TRANSFER_SIZE 32
#elif defined(ENABLE_SAFE_PATH)
#define TRANSFER_SIZE 16
#endif

int main()
{
    int buffer[TRANSFER_SIZE] = {0};
    return buffer[0];
}
