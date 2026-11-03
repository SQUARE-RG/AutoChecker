int main()
{
    float f = 0.0f;
    float g = 1.0f;
    for (f = 0.0f; f < 10.0f; f = f + 1.0f) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-2]
    {
        g = f + g;
    }
    return 0;
}
