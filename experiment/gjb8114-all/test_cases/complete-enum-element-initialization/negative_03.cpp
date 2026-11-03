int main()
{
    enum Color
    {
        RED,
        GREEN,
        BLUE = 7 // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-4]
    };
    Color c = BLUE;
    return static_cast<int>(c);
}
