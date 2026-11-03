static int square_with_local_macro(int value)
{
#define LOCAL_SQUARE(x) ((x) * (x)) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-6]
    return LOCAL_SQUARE(value);
}

int main()
{
    return square_with_local_macro(2);
}
