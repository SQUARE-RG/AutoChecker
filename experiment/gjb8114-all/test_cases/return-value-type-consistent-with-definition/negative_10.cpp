enum Color
{
    kRed = 1,
    kGreen = 2
};

int color_code()
{
    Color color = kGreen;
    return color; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-10]
}

int main()
{
    int code = color_code();
    return (code == 2) ? 0 : 1;
}
