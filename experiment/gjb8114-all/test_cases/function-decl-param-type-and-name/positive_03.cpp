void process(int &value, int array[10]);

int main() {
    int x = 1;
    int arr[10] = {};
    process(x, arr);
    return 0;
}

void process(int &value, int array[10]) {
    value += array[0];
}
