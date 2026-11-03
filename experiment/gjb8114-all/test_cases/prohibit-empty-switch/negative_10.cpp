int main()
{
    int value = 0;
    switch (value)
    {
    case 0:
        switch (value) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-3]
        }
        break;
    default:
        break;
    }
    return 0;
}
