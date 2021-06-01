# older version of the anagrams method of the Lexicon class

	def anagrams(self, word, busyWait=None):
		'''Return a list of anagrams of word. If busyWait is not None,
		it must be either a function or a method which will get called
		at the beginning, at the start of each 1,000 permutations checked,
		and at the end with an argument indicating the current permutation
		count, or -1 at the end.'''
		def anagrams_aux(dst, src, found):
			if len(src) == 0:   # base case, all letters used
				if busyWait:
					nonlocal busyCount
					if busyCount % 1000 == 0:
						# Python automagically adds the first 'self' argument
						# if busyWait is in fact a method
						busyWait(busyCount)
					busyCount += 1
				result = self.contains(dst)
				if result and result not in found:
					found.append(result)
			else:
				for i in range(len(src)):
					anagrams_aux(dst + src[i], src[:i] + src[i+1:], found)
		if busyWait:
			busyCount = 0
		if self.caseInsensitive:
			word = word.upper()
		results = []
		anagrams_aux('', word, results)
		if busyWait:
			busyWait(-1)
		return results

