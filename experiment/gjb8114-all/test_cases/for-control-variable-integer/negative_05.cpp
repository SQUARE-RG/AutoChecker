int main()
{
    for (float f = 1.0f; f != 1024.0f; f *= 2.0f) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-2]
    {
    }
    return 0;
}
