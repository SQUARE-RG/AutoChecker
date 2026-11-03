double g_double = 0.0;

int main()
{
    float f = 0.0f;
    f = g_double; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-3]
    return 0;
}
