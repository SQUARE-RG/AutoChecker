enum WorkMode { INI = 0, FIGHT, MAINTAIN, TRAIN };

int main()
{
    WorkMode work_state = INI;
    int i = 0;

    switch (work_state)
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
        case TRAIN:
            i = 0;
            break;
    }

    return i;
}
