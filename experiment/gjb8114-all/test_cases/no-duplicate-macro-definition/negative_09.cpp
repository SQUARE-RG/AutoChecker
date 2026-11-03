#define FEATURE_FLAG

int compute(void)
{
#ifdef FEATURE_FLAG
    return 1;
#else
    return 0;
#endif
}

#define FEATURE_FLAG 7 // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-5]

int main(void)
{
    return compute() + FEATURE_FLAG;
}
