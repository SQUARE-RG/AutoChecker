unsigned int compute_value()
{
    unsigned int value = 0U;
#define LOCAL_FACTOR 3U // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-6]
    value = value + LOCAL_FACTOR;
    return value;
}

int main()
{
    return static_cast<int>(compute_value());
}
