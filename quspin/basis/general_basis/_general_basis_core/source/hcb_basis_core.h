
#ifndef _HCB_BASIS_OP_H
#define _HCB_BASIS_OP_H

#include <complex>
#include "general_basis_core.h"
#include "numpy/ndarraytypes.h"

template<class I>
I inline hcb_map_bits(I s,const int map[],const int N){
	I ss = 0;
	for(int i=0;i<N;i++){
		int j = map[i];
		ss ^= ( j<0 ? ((s&1)^1)<<(-(j+1)) : (s&1)<<j );
		s >>= 1;
	}
	return ss;
}


template<class I>
class hcb_basis_core : public general_basis_core<I>
{
	public:
		hcb_basis_core(const int _N,const int _nt,const int _maps[], \
		const int _rev_maps[], const int _pers[], const int _qs[]) : \
		general_basis_core<I>::general_basis_core(_N,_nt,_maps,_rev_maps,_pers,_qs) {}

		~hcb_basis_core() {}

		const map_func_type<I> map_func = &hcb_map_bits<I>;

		void map_state(I s[],npy_intp M,int n_map){
			const int n = general_basis_core<I>::N;
			for(npy_intp i=0;i<M;i++){
				s[i] = map_func(s[i],&general_basis_core<I>::maps[n_map*n],n);
			}
		}

		bool check_state(I s){
			return check_state_core<I>(map_func,s,s,general_basis_core<I>::maps, \
				general_basis_core<I>::pers,general_basis_core<I>::qs, \
				general_basis_core<I>::nt,general_basis_core<I>::N);
		}

		I ref_state(I s,int g[]){
			int gg[general_basis_core<I>::nt];
			for(int i=0;i<general_basis_core<I>::nt;i++){
				g[i] = 0;
				gg[i] = 0;
			}
			return ref_state_core<I>(map_func,s,general_basis_core<I>::maps,\
				general_basis_core<I>::pers,general_basis_core<I>::nt,general_basis_core<I>::nt,\
				general_basis_core<I>::N,s,g,gg);
		}

		double get_norm(I s){
			return get_norm_core<I>(map_func,s,s,general_basis_core<I>::maps,general_basis_core<I>::rev_maps,\
				general_basis_core<I>::pers,general_basis_core<I>::qs,general_basis_core<I>::nt,general_basis_core<I>::N);
		}

		I inline next_state_pcon(I s){
			if(s==0){return s;}
			I t = (s | (s - 1)) + 1;
			return t | ((((t & -t) / (s & -s)) >> 1) - 1);
		}

		int op(I &r,std::complex<double> &m,const int n_op,const unsigned char opstr[],const int indx[]){
			I s = r;
			for(int j=n_op-1;j>-1;j--){
				int ind = general_basis_core<I>::N-indx[j]-1;
				I b = (1ull << ind);
				bool a = (r >> ind)&1;
				char op = opstr[j];
				switch(op){
					case 'z':
						m *= (a?0.5:-0.5);
						break;
					case 'x':
						r ^= b;
						m *= 0.5;
						break;
					case 'y':
						m *= (a?std::complex<double>(0,0.5):std::complex<double>(0,-0.5));
						r ^= b;
						break;
					case '+':
						m *= (a?0:1);
						r ^= b;
						break;
					case '-':
						m *= (a?1:0);
						r ^= b;
						break;
					case 'I':
						break;
					default:
						return -1;
				}

				if(std::abs(m)==0){
					r = s;
					break;
				}
			}

			return 0;
		}
};







#endif
