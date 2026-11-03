namespace
{
    int wait_for_signal()
    {
        bool ready = false;

        while (true) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-4]
        {
            ready = true;
            if (ready)
            {
                return 0;
            }
        }
    }
}

int main()
{
    return wait_for_signal();
}
