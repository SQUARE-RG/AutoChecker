#define IN_RANGE(value, low, high) ((value) >= (low) && (value) <= (high))

int main()
{
    int value = 4;
    int low = 1;
    int high = 3;
    int result = IN_RANGE(value, low, high + 1) ? 0 : 1;
    return result;
}
