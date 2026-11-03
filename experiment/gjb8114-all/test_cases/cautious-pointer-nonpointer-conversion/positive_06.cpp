typedef int* IntPtr;

int main() {
    int x = 1;
    IntPtr p = &x;
    IntPtr q = p;
    int whole = int(2.5);
    return whole + *q;
}
