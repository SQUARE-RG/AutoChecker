#define DEREF(p) (*(p))

int main()
{
    int arr[3] = {1, 2, 3};
    int *base = arr;
    int value = DEREF(base + 1);
    return value;
}
