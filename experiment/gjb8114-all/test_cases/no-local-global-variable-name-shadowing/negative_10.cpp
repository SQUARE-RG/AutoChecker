int mode = 0;

int main()
{
    switch (int mode = 1; mode) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-1]
        case 0:
            break;
        default:
            break;
    }
    return mode;
}
