int main() {
    int* values = new int[2];
    values[0] = 3;
    values[1] = 5;
    int result = values[0] + values[1];
    delete[] values;
    return result;
}
