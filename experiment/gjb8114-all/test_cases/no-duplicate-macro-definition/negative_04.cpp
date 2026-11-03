#define BUFFER_LIMIT 64

int main()
{
#define BUFFER_LIMIT 128 // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-5]
    int size = BUFFER_LIMIT;
    (void)size;
    return 0;
}
