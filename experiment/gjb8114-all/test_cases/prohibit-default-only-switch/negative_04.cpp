int main()
{
    int outer = 0;
    switch (outer)
    {
        case 0:
            break;
        default:
        {
            int inner = 0;
            switch (inner)
            {
                default:
                {
                    inner += 1;
                    break;
                }
            } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-5]
            outer += 1;
            break;
        }
    }
    return outer;
}
