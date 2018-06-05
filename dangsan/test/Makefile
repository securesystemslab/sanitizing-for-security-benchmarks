all: test01.dangsan

%.o : %.c
	$(CC) $(CFLAGS) -o $@ -c $<

%.dangsan : %.o
	$(LD) $(LDFLAGS) -o $@ $<

.PHONY: clean test

test:
	./test01.dangsan

clean:
	$(RM) *.dangsan *.o
