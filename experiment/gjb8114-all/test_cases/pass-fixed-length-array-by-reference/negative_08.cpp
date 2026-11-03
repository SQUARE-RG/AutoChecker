struct Record {
    int id;
};

void reset_records(Record records[4]) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-1]
{
    for (int i = 0; i < 4; ++i) {
        records[i].id = 0;
    }
}

int main() {
    Record records[4] = {{1}, {2}, {3}, {4}};
    reset_records(records);
    return 0;
}
