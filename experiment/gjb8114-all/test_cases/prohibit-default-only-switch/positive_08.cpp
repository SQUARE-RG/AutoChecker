int shared_case_body(int value)
{
    switch (value) {
        case 1:
        case 2:
            return value + 1;
    }
    return 0;
}
