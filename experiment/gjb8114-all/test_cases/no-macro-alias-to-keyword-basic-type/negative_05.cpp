#define SWITCH switch // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-2]

int main()
{
    int value = 2;
    SWITCH (value)
    {
    case 1:
        value = 10;
        break;
    case 2:
        value = 20;
        break;
    default:
        break;
    }
    return value;
}
