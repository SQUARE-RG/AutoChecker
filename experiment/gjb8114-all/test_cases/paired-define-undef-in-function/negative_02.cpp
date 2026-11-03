#define FEATURE_LIMIT 64

int clamp_value(int value)
{
    int result = value > FEATURE_LIMIT ? FEATURE_LIMIT : value;
#undef FEATURE_LIMIT // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-6]
    return result;
}

int main()
{
    return clamp_value(100);
}
