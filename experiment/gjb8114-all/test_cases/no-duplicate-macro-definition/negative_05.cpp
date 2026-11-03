#define CONVERT(x) ((x) * 2)

static int twice(int value)
{
    return CONVERT(value);
}

#define CONVERT 42 // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-5]

int main()
{
    int result = CONVERT;
    return result + twice(3);
}
