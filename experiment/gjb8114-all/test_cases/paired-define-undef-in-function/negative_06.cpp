unsigned int compute(void)
{
    unsigned int result = 0U;
#define LOCAL_MACRO 5U
    result = result + LOCAL_MACRO;
#undef OTHER_MACRO // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-6]
#undef LOCAL_MACRO
    return result;
}

int main()
{
    return (compute() == 5U) ? 0 : 1;
}
