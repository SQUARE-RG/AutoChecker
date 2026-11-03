#define FEATURE_ENABLED 1

#if FEATURE_ENABLED
#define BUFFER_SIZE 128
#endif

#define BUFFER_SIZE 256 // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-5]

int main(void)
{
    return BUFFER_SIZE;
}
