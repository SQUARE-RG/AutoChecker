int select_value(int selector)
{
    int value = 0;
    switch (selector)
    {
        case 1:
            value = 10;
            break;
            value = 20; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-1]
        case 2:
            value = 30;
            break;
        default:
            value = 40;
            break;
    }
    return value;
}

int main(int argc, char** argv)
{
    return select_value(argc);
}
