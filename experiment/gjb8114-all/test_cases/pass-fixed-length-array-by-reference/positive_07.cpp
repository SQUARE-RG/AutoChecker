void clear_all(int* (&values)[5])
{
    for (int i = 0; i < 5; ++i) {
        values[i] = nullptr;
    }
}

int main() {
    int a = 1;
    int b = 2;
    int c = 3;
    int d = 4;
    int e = 5;
    int* arr[5] = {&a, &b, &c, &d, &e};
    clear_all(arr);
    return 0;
}
