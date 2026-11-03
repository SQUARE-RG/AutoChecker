enum WorkMode { INI = 0, FIGHT, MAINTAIN, TRAIN };

int main()
{
    WorkMode work_state = INI;
    int i = 0;

    switch (work_state) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-6]
    {
        case INI:
            i = 1;
            break;
        case FIGHT:
            i = 2;
            break;
        case MAINTAIN:
            i = 3;
            break;
    }

    return i;
}
