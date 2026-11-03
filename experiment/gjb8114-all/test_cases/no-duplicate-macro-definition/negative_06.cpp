#define ENABLE_DEBUG 1

#if ENABLE_DEBUG
#define DEBUG_LEVEL 1
#endif

#if ENABLE_DEBUG
#define DEBUG_LEVEL 2 // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-5]
#endif

int main()
{
    return DEBUG_LEVEL;
}
