int classify(int n)
{
    switch (n) {
    case 9:
        return 1;
    case 010:
        // CHECK-MESSAGES: :[[@LINE-1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-4]
        return 2;
    default:
        return 0;
    }
}
