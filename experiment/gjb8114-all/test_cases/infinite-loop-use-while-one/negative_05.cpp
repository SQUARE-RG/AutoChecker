int Gstate = 0;

void wait_for_ready()
{
    while (true) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-4]
    {
        if (Gstate == 1)
        {
            break;
        }
    }
}

int main()
{
    wait_for_ready();
    return 0;
}
