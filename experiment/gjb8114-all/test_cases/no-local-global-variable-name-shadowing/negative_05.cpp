int counter = 0;

int main()
{
    counter = 10;
    int source = 3;
    while (int counter = source--) {   // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-1]
        break;
    }
    return 0;
}
