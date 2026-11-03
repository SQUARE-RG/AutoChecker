#define BEGIN_SWITCH(x) switch (x) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-2]

int main()
{
    int value = 1;
    int result = 0;

    BEGIN_SWITCH(value)
    case 1:
        result = 10;
        break;
    default:
        result = 20;
        break;
    }

    return result == 10 ? 0 : 1;
}
