unsigned int compute(void)
{
    unsigned int result = 0U;
#define LOCAL_MACRO 2U
    result = result + LOCAL_MACRO;
#undef LOCAL_MACRO
#define EXTRA_MACRO 1U // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-6]
    result = result + EXTRA_MACRO;
    return result;
}

int main()
{
    return (compute() == 3U) ? 0 : 1;
}
