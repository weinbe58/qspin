from __future__ import print_function, division

import sys,os
qspin_path = os.path.join(os.getcwd(),"../")
sys.path.insert(0,qspin_path)


from qspin.basis import spin_basis_1d,photon_basis # Hilbert space bases
from qspin.operators import hamiltonian, exp_op # Hamiltonian and observables
from qspin.tools.measurements import obs_vs_time,ED_state_vs_time
import numpy as np
from numpy.random import uniform,seed,shuffle,randint # pseudo random numbers
seed()


"""
This test only makes sure the function 'obs_vs_time' runs properly.
"""

dtypes={"float64":np.float64,"complex128":np.complex128}

dtypes={
		"float32":np.float32,
		"float64":np.float64,
		"complex64":np.complex64,
		"complex128":np.complex128
		}

atols={"float32":1E-4,"float64":1E-13,"complex64":1E-4,"complex128":1E-13}
rtols={"float32":1E-4,"float64":1E-13,"complex64":1E-4,"complex128":1E-13}


def drive(t):
	return np.exp(-0.2*t)*np.cos(1.7*t)
drive_args=[]

def time_dep(t):
	return np.cosh(+1.1*t)*np.cos(2.0*t)

solver_atol = 1E-18
solver_rtol = 1E-18


L=10
basis = spin_basis_1d(L)

Jzxz=uniform(3.0)
Jzz=uniform(3.0)
Jxy=uniform(3.0)
Jyy=uniform(3.0)

J_zxz =[[Jzxz,i,(i+1)%L,(i+2)%L] for i in range(0,L)]
J_zz = [[Jzz,i,(i+1)%L] for i in range(0,L)] 
J_xy = [[Jxy,i,(i+1)%L] for i in range(0,L)]
J_yy = [[Jyy,i,(i+1)%L] for i in range(0,L)]
# static and dynamic lists
static_pm = [["+-",J_xy],["-+",J_xy]]
static_yy = [["yy",J_yy]]
dynamic_zz = [["zz",J_zz,time_dep,drive_args]]
dynamic_zxz = [["zxz",J_zxz,drive,drive_args]]

t=np.linspace(0.0,2.0,20)

for _i in dtypes.keys():
	dtype = dtypes[_i]
	atol = atols[_i]
	rtol = rtols[_i]

	H=hamiltonian(static_pm,dynamic_zxz,basis=basis,dtype=dtype,check_herm=False,check_symm=False)
	Ozz=hamiltonian([],dynamic_zz,basis=basis,dtype=dtype,check_herm=False,check_symm=False)
	H2=hamiltonian(static_yy,[],basis=basis,dtype=dtype,check_herm=False,check_symm=False) 

	_,psi0 = H.eigsh(time=0,k=1,sigma=-100.0)
	psi0=psi0.squeeze()

	psi_t=H.evolve(psi0,0.0,t,iterate=True,rtol=solver_rtol,atol=solver_atol)
	psi_t2=H.evolve(psi0,0.0,t,rtol=solver_rtol,atol=solver_atol)

	Obs_list = {"Ozz_t":Ozz,"Ozz":Ozz(time=np.sqrt(np.exp(0.0)) )} 
	Sent_args={'basis':basis,'chain_subsys':range( L//2 )}

	Obs = obs_vs_time(psi_t,t,Obs_list,return_state=True,Sent_args=Sent_args)
	Obs2 = obs_vs_time(psi_t2,t,Obs_list,return_state=True,Sent_args=Sent_args)

	Expn = np.array([Obs['Ozz_t'],Obs['Ozz']])
	psi_t = Obs['psi_t']
	Sent = Obs['Sent_time']['Sent']

	Expn2 = np.array([Obs2['Ozz_t'],Obs2['Ozz']])
	psi_t2 = Obs2['psi_t']
	Sent2 = Obs2['Sent_time']['Sent']


	np.testing.assert_allclose(Expn,Expn2,atol=atol,rtol=rtol,err_msg='Failed observable comparison!')
	np.testing.assert_allclose(psi_t,psi_t2,atol=atol,rtol=rtol,err_msg='Failed state comparison!')
	np.testing.assert_allclose(Sent,Sent2,atol=atol,err_msg='Failed ent entropy comparison!')

	### check obs_vs_time vs ED

	E,V = H2.eigh()

	psi_t=H2.evolve(psi0,0.0,t,iterate=False,rtol=solver_rtol,atol=solver_atol)
	psi_t4=exp_op(H2,a=-1j,start=0.0,stop=2.0,num=20,endpoint=True,iterate=True).dot(psi0)


	Obs = obs_vs_time(psi_t,t,Obs_list,return_state=True,Sent_args=Sent_args)
	Obs2 = obs_vs_time((psi0,E,V),t,Obs_list,return_state=True,Sent_args=Sent_args)
	Obs4 = obs_vs_time(psi_t4,t,Obs_list,return_state=True,Sent_args=Sent_args)

	psi_t3 = ED_state_vs_time(psi0,E,V,t,iterate=False)
	psi_t33 = np.asarray([psi for psi in ED_state_vs_time(psi0,E,V,t,iterate=True)]).T


	Expn = np.array([Obs['Ozz_t'],Obs['Ozz']])
	psi_t = Obs['psi_t']
	Sent = Obs['Sent_time']['Sent']

	Expn2 = np.array([Obs2['Ozz_t'],Obs2['Ozz']])
	psi_t2 = Obs2['psi_t']
	Sent2 = Obs2['Sent_time']['Sent']

	Expn4 = np.array([Obs4['Ozz_t'],Obs4['Ozz']])
	psi_t4 = Obs4['psi_t']
	Sent4 = Obs4['Sent_time']['Sent']

	np.testing.assert_allclose(Expn,Expn2,atol=atol,rtol=rtol,err_msg='Failed observable comparison!')
	np.testing.assert_allclose(psi_t,psi_t2,atol=atol,rtol=rtol,err_msg='Failed state comparison!')
	np.testing.assert_allclose(Sent,Sent2,atol=atol,rtol=rtol,err_msg='Failed ent entropy comparison!')
	np.testing.assert_allclose(psi_t2,psi_t3,atol=atol,rtol=rtol,err_msg='Failed ED_state_vs_time test!')
	np.testing.assert_allclose(psi_t3,psi_t33,atol=atol,rtol=rtol,err_msg='Failed ED_state_vs_time test!')
	np.testing.assert_allclose(psi_t2,psi_t4,atol=atol,rtol=rtol,err_msg='Failed exp_op test!')


print("obs_vs_time checks passed!")


