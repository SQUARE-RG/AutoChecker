int Gstate = 0;

void poll_state()
{
    for (;;) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-4]
    {
        if (Gstate == 2)
        {
            goto finished;
        }
    }
finished:
    return;
}

int main()
{
    poll_state();
    return 0;
}
