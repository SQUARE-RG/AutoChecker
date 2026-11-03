int main()
{
    float measurement = 0.1f;
    if (measurement == 0.1f) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-3]
        return 1;
    }
    return 0;
}
