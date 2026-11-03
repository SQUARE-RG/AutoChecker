int main()
{
    int i = 0;
    int j = 0;

    switch (i) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-6]
    {
        case 0:
            j = 0;
            break;
        case 1:
        case 2:
            j = 1;
            break;
    }

    return j;
}
