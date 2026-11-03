enum Status { idle = 0, busy = 1 };

int main()
{
    unsigned int counter = 0;
    counter += busy; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-11]
    return 0;
}
