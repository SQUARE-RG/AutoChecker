#define SELECT_OR_ZERO(flag, value) ((flag) ? (value) : 0)

int main()
{
    int flag = 1;
    int value = 7;
    int result = 2 + SELECT_OR_ZERO(flag, value);
    return result;
}
